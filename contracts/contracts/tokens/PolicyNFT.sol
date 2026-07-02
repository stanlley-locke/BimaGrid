// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract PolicyNFT is ERC721URIStorage, Ownable {
    uint256 private _tokenIds;

    event PolicyNFTMinted(uint256 indexed tokenId, address indexed farmer, string tokenURI);

    constructor() ERC721("BimaGrid Policy NFT", "BIMAPOL") {}

    function mintPolicyNFT(address farmer, string memory tokenURI) external onlyOwner returns (uint256) {
        _tokenIds++;
        uint256 newItemId = _tokenIds;
        _mint(farmer, newItemId);
        _setTokenURI(newItemId, tokenURI);

        emit PolicyNFTMinted(newItemId, farmer, tokenURI);
        return newItemId;
    }
}
