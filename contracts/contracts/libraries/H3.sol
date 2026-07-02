// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

library H3 {
    // Standard H3 Index bitmask offsets
    uint8 private constant MODE_OFFSET = 59;
    uint8 private constant RESOLUTION_OFFSET = 52;
    
    /**
     * @dev Validates whether a bytes32 payload represents a structurally valid H3 index.
     * H3 indices are 64-bit unsigned integers, stored left-padded (or big-endian) in bytes32.
     */
    function isValidH3Index(bytes32 h3Index) internal pure returns (bool) {
        uint256 value = uint256(h3Index);
        if (value == 0) return false;
        
        // Extract Mode (bits 59-62)
        // H3 standard index mode is 1 (cell)
        uint256 mode = (value >> MODE_OFFSET) & 0xF;
        if (mode != 1) return false;
        
        // Extract Resolution (bits 52-55)
        uint256 resolution = (value >> RESOLUTION_OFFSET) & 0xF;
        if (resolution > 15) return false;
        
        return true;
    }
}
