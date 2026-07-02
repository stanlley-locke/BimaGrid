const { expect } = require("chai");
const { ethers } = require("hardhat");
const { packH3Index } = require("../../utils/h3-helper");
const { signReport } = require("../../utils/crypto-helper");

describe("BimaGrid Parametric Insurance Core", function () {
  let policyRegistry, escrowVault, mitigationVerifier, oracle;
  let owner, oracle1, oracle2, oracle3, farmer, attacker;
  let h3Index;
  const timestamp = Math.floor(Date.now() / 1000);
  const premium = ethers.parseEther("0.1");
  const payoutAmount = BigInt(ethers.parseEther("1.0"));
  const threshold = 2000n; // 20.00 mm

  beforeEach(async function () {
    [owner, oracle1, oracle2, oracle3, farmer, attacker] = await ethers.getSigners();
    h3Index = packH3Index("8928308280fffff");

    const PolicyRegistry = await ethers.getContractFactory("PolicyRegistry");
    policyRegistry = await PolicyRegistry.deploy();

    const EscrowVault = await ethers.getContractFactory("EscrowVault");
    escrowVault = await EscrowVault.deploy();

    const MitigationVerifier = await ethers.getContractFactory("MitigationVerifier");
    mitigationVerifier = await MitigationVerifier.deploy();

    const KilimaShieldOracle = await ethers.getContractFactory("KilimaShieldOracle");
    oracle = await KilimaShieldOracle.deploy(
      await policyRegistry.getAddress(),
      await escrowVault.getAddress()
    );

    await policyRegistry.setAuthorizedCaller(await oracle.getAddress(), true);
    await escrowVault.setAuthorizedCaller(await oracle.getAddress(), true);

    // Fund escrow vault
    await owner.sendTransaction({
      to: await escrowVault.getAddress(),
      value: ethers.parseEther("5.0"),
    });

    await oracle.setAuthorizedOracle(oracle1.address, true);
    await oracle.setAuthorizedOracle(oracle2.address, true);
    await oracle.setAuthorizedOracle(oracle3.address, true);
  });

  // ─── Helpers ──────────────────────────────────────────────────────────────
  async function registerPolicy(policyId = 123) {
    await oracle.registerPolicy(policyId, farmer.address, h3Index, threshold, payoutAmount, {
      value: premium,
    });
  }

  async function oracleSig(signer, rainfall, ndvi) {
    return signReport(signer, h3Index, timestamp, rainfall, ndvi);
  }

  // ─── 1. Policy Registration ───────────────────────────────────────────────
  describe("PolicyRegistry", function () {
    it("Should register a policy and store all fields", async function () {
      await registerPolicy(99);
      const p = await policyRegistry.policies(99);
      expect(p.farmer).to.equal(farmer.address);
      expect(p.threshold).to.equal(threshold);
      expect(p.payoutAmount).to.equal(payoutAmount);
      expect(p.isActive).to.be.true;
      expect(p.paidOut).to.be.false;
    });

    it("Should revert duplicate policy registration with custom error", async function () {
      await registerPolicy(100);
      await expect(registerPolicy(100)).to.be.revertedWithCustomError(
        policyRegistry, "PolicyAlreadyExists"
      );
    });

    it("Should deposit premium into escrow on registration", async function () {
      await registerPolicy(101);
      const escrowPremium = await escrowVault.premiums(101);
      expect(escrowPremium).to.equal(premium);
    });

    it("Should allow policy deactivation by authorized caller", async function () {
      await registerPolicy(102);
      await policyRegistry.setAuthorizedCaller(owner.address, true);
      await policyRegistry.deactivatePolicy(102);
      const p = await policyRegistry.policies(102);
      expect(p.isActive).to.be.false;
    });

    it("Should reject registration without premium", async function () {
      await expect(
        oracle.registerPolicy(103, farmer.address, h3Index, threshold, payoutAmount, { value: 0 })
      ).to.be.revertedWithCustomError(oracle, "PremiumRequired");
    });

    it("Should reject registerPolicy to zero farmer address", async function () {
      await expect(
        oracle.registerPolicy(104, ethers.ZeroAddress, h3Index, threshold, payoutAmount, {
          value: premium,
        })
      ).to.be.revertedWithCustomError(policyRegistry, "ZeroAddress");
    });
  });

  // ─── 2. Oracle Signature & Consensus ─────────────────────────────────────
  describe("Oracle Signature and Consensus", function () {
    beforeEach(async () => registerPolicy());

    it("Should accept valid signature from authorized oracle", async function () {
      const sig = await oracleSig(oracle1, 1500, 5000);
      await expect(oracle.submitData(h3Index, timestamp, 1500, 5000, sig))
        .to.emit(oracle, "DataSubmitted")
        .withArgs(oracle1.address, h3Index, timestamp);
    });

    it("Should reject submission from unauthorized signer (custom error)", async function () {
      const sig = await oracleSig(attacker, 1500, 5000);
      await expect(oracle.submitData(h3Index, timestamp, 1500, 5000, sig))
        .to.be.revertedWithCustomError(oracle, "UnauthorizedOracle");
    });

    it("Should reject duplicate submission from same oracle (custom error)", async function () {
      const sig = await oracleSig(oracle1, 1500, 5000);
      await oracle.submitData(h3Index, timestamp, 1500, 5000, sig);
      await expect(oracle.submitData(h3Index, timestamp, 1500, 5000, sig))
        .to.be.revertedWithCustomError(oracle, "DuplicateSubmission");
    });

    it("Should trigger payout when consensus median is below threshold", async function () {
      const sig1 = await oracleSig(oracle1, 1500, 5000);
      const sig2 = await oracleSig(oracle2, 1800, 5000);
      const sig3 = await oracleSig(oracle3, 1200, 5000);

      await oracle.submitData(h3Index, timestamp, 1500, 5000, sig1);
      await oracle.submitData(h3Index, timestamp, 1800, 5000, sig2);

      const before = await ethers.provider.getBalance(farmer.address);

      await expect(oracle.submitData(h3Index, timestamp, 1200, 5000, sig3))
        .to.emit(oracle, "ConsensusReached")
        .withArgs(h3Index, timestamp, 1500, 5000)
        .to.emit(oracle, "PayoutTriggered")
        .withArgs(123, farmer.address, payoutAmount);

      const after = await ethers.provider.getBalance(farmer.address);
      expect(after - before).to.equal(payoutAmount);

      const p = await policyRegistry.policies(123);
      expect(p.paidOut).to.be.true;
      expect(p.isActive).to.be.false;
    });

    it("Should NOT trigger payout when consensus median is above threshold", async function () {
      const sig1 = await oracleSig(oracle1, 2500, 5000);
      const sig2 = await oracleSig(oracle2, 2800, 5000);
      const sig3 = await oracleSig(oracle3, 2200, 5000);

      await oracle.submitData(h3Index, timestamp, 2500, 5000, sig1);
      await oracle.submitData(h3Index, timestamp, 2800, 5000, sig2);
      await expect(oracle.submitData(h3Index, timestamp, 2200, 5000, sig3))
        .to.emit(oracle, "ConsensusReached")
        .withArgs(h3Index, timestamp, 2500, 5000)
        .not.to.emit(oracle, "PayoutTriggered");

      const p = await policyRegistry.policies(123);
      expect(p.paidOut).to.be.false;
      expect(p.isActive).to.be.true;
    });

    it("Should only payout once even on repeated consensus (already paidOut)", async function () {
      const ts2 = timestamp + 86400;

      // ── Round 1: triggers drought payout ──────────────────────────────────
      const sig1 = await oracleSig(oracle1, 1500, 5000);
      const sig2 = await oracleSig(oracle2, 1800, 5000);
      const sig3 = await oracleSig(oracle3, 1200, 5000);

      await oracle.submitData(h3Index, timestamp, 1500, 5000, sig1);
      await oracle.submitData(h3Index, timestamp, 1800, 5000, sig2);
      await oracle.submitData(h3Index, timestamp, 1200, 5000, sig3);

      // ── Round 2: sign with ts2 so ECDSA recovery resolves correctly ───────
      // oracleSig uses module-level `timestamp` — must call signReport directly
      const sig1b = await signReport(oracle1, h3Index, ts2, 1400, 4500);
      const sig2b = await signReport(oracle2, h3Index, ts2, 1600, 4500);
      const sig3b = await signReport(oracle3, h3Index, ts2, 1300, 4500);

      await oracle.submitData(h3Index, ts2, 1400, 4500, sig1b);
      await oracle.submitData(h3Index, ts2, 1600, 4500, sig2b);
      // Policy already paidOut=true — consensus fires but no PayoutTriggered
      await expect(oracle.submitData(h3Index, ts2, 1300, 4500, sig3b))
        .not.to.emit(oracle, "PayoutTriggered");
    });
  });

  // ─── 3. EscrowVault ───────────────────────────────────────────────────────
  describe("EscrowVault", function () {
    it("Should revert payout with custom error when insufficient balance", async function () {
      const emptyVault = await (await ethers.getContractFactory("EscrowVault")).deploy();
      await emptyVault.setAuthorizedCaller(owner.address, true);
      await expect(
        emptyVault.payout(1, farmer.address, ethers.parseEther("10"))
      ).to.be.revertedWithCustomError(emptyVault, "InsufficientBalance");
    });

    it("Should allow pull-payment refund claim", async function () {
      const vault = await (await ethers.getContractFactory("EscrowVault")).deploy();
      await vault.setAuthorizedCaller(owner.address, true);
      await owner.sendTransaction({ to: await vault.getAddress(), value: ethers.parseEther("1.0") });

      await vault.refundPremium(1, farmer.address, ethers.parseEther("0.5"));
      expect(await vault.pendingRefunds(farmer.address)).to.equal(ethers.parseEther("0.5"));

      const before = await ethers.provider.getBalance(farmer.address);
      const tx = await vault.connect(farmer).claimRefund();
      const receipt = await tx.wait();
      const gasCost = receipt.gasUsed * tx.gasPrice;
      const after = await ethers.provider.getBalance(farmer.address);

      expect(after + gasCost - before).to.equal(ethers.parseEther("0.5"));
      expect(await vault.pendingRefunds(farmer.address)).to.equal(0n);
    });

    it("Should revert claimRefund with NoPendingRefund when balance is zero", async function () {
      await expect(escrowVault.connect(farmer).claimRefund())
        .to.be.revertedWithCustomError(escrowVault, "NoPendingRefund");
    });
  });

  // ─── 4. MitigationVerifier ────────────────────────────────────────────────
  describe("MitigationVerifier", function () {
    it("Should add mitigation and calculate cumulative discount correctly", async function () {
      await mitigationVerifier.verifyMitigation(1, "drip_irrigation"); // 15%
      await mitigationVerifier.verifyMitigation(1, "soil_bunds");       // 10%
      const discount = await mitigationVerifier.calculateDiscount(1);
      expect(discount).to.equal(2500n); // 25%
    });

    it("Should cap total discount at 50% (5000 basis points)", async function () {
      await mitigationVerifier.verifyMitigation(2, "drip_irrigation"); // 15%
      await mitigationVerifier.verifyMitigation(2, "soil_bunds");      // 10%
      await mitigationVerifier.verifyMitigation(2, "mulching");        // 5%
      await mitigationVerifier.verifyMitigation(2, "drip_irrigation"); // 15% again
      await mitigationVerifier.verifyMitigation(2, "drip_irrigation"); // 15% again
      const discount = await mitigationVerifier.calculateDiscount(2);
      expect(discount).to.equal(5000n); // capped at 50%
    });

    it("Should update mitigation discount via owner", async function () {
      await mitigationVerifier.setMitigationDiscount("solar_pump", 2000); // 20%
      expect(await mitigationVerifier.mitigationDiscounts("solar_pump")).to.equal(2000n);
    });
  });

  // ─── 5. Oracle Management ─────────────────────────────────────────────────
  describe("Oracle Management", function () {
    it("Should track oracle count correctly on authorize/deauthorize", async function () {
      const count = await oracle.oracleCount();
      expect(count).to.equal(3n);
      await oracle.setAuthorizedOracle(oracle3.address, false);
      expect(await oracle.oracleCount()).to.equal(2n);
    });

    it("Should revert setAuthorizedOracle for zero address", async function () {
      await expect(oracle.setAuthorizedOracle(ethers.ZeroAddress, true))
        .to.be.revertedWithCustomError(oracle, "InvalidOracleAddress");
    });
  });

  // ─── 6. Median calculation ────────────────────────────────────────────────
  describe("getMedian", function () {
    it("a <= b <= c → b", async () => expect(await oracle.getMedian(1, 2, 3)).to.equal(2n));
    it("c <= b <= a → b", async () => expect(await oracle.getMedian(3, 2, 1)).to.equal(2n));
    it("b <= a <= c → a", async () => expect(await oracle.getMedian(2, 1, 3)).to.equal(2n));
    it("all equal → any value", async () => expect(await oracle.getMedian(5, 5, 5)).to.equal(5n));
    it("large values", async () => expect(await oracle.getMedian(99999, 11111, 55555)).to.equal(55555n));
  });
});
