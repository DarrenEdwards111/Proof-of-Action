// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

import "./interfaces/IProofOfAction.sol";

/**
 * @title MikoToken
 * @dev ERC-20 token with Proof-of-Action minting policy
 * 
 * Key Features:
 * - Uncapped supply (minted on verified action)
 * - One-time proof usage (prevents double-minting)
 * - Oracle-controlled minting authority
 * - Standard burn functionality
 */
contract MikoToken is IMikoToken {
    string public constant name = "Mikoshi Coin";
    string public constant symbol = "MIKO";
    uint8 public constant decimals = 18;

    uint256 private _totalSupply;
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    mapping(bytes32 => bool) private _usedProofs;

    address public oracle;
    address public owner;

    modifier onlyOracle() {
        require(msg.sender == oracle, "MikoToken: caller is not oracle");
        _;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "MikoToken: caller is not owner");
        _;
    }

    constructor(address _oracle) {
        require(_oracle != address(0), "MikoToken: oracle is zero address");
        oracle = _oracle;
        owner = msg.sender;
    }

    // ==================== ERC-20 Functions ====================

    function totalSupply() external view override returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) external view override returns (uint256) {
        return _balances[account];
    }

    function transfer(address to, uint256 amount) external override returns (bool) {
        _transfer(msg.sender, to, amount);
        return true;
    }

    function allowance(address _owner, address spender) external view override returns (uint256) {
        return _allowances[_owner][spender];
    }

    function approve(address spender, uint256 amount) external override returns (bool) {
        _approve(msg.sender, spender, amount);
        return true;
    }

    function transferFrom(address from, address to, uint256 amount) external override returns (bool) {
        uint256 currentAllowance = _allowances[from][msg.sender];
        require(currentAllowance >= amount, "MikoToken: insufficient allowance");
        
        _transfer(from, to, amount);
        _approve(from, msg.sender, currentAllowance - amount);
        return true;
    }

    // ==================== Proof-of-Action Functions ====================

    /**
     * @dev Mints new tokens upon verified action
     * @param to Recipient address (actor who performed the action)
     * @param amount Token amount to mint
     * @param proofHash Unique hash commitment of the verified action
     * 
     * Requirements:
     * - Caller must be authorized oracle
     * - Proof hash must not have been used before
     */
    function mint(address to, uint256 amount, bytes32 proofHash) external override onlyOracle {
        require(to != address(0), "MikoToken: mint to zero address");
        require(!_usedProofs[proofHash], "MikoToken: proof already used");
        require(proofHash != bytes32(0), "MikoToken: invalid proof hash");

        _usedProofs[proofHash] = true;
        _totalSupply += amount;
        _balances[to] += amount;

        emit Mint(to, amount, proofHash);
        emit Transfer(address(0), to, amount);
    }

    /**
     * @dev Burns tokens from caller's balance
     * @param amount Token amount to burn
     */
    function burn(uint256 amount) external override {
        require(_balances[msg.sender] >= amount, "MikoToken: burn amount exceeds balance");

        _balances[msg.sender] -= amount;
        _totalSupply -= amount;

        emit Burn(msg.sender, amount);
        emit Transfer(msg.sender, address(0), amount);
    }

    /**
     * @dev Checks if a proof hash has been used for minting
     */
    function isProofUsed(bytes32 proofHash) external view override returns (bool) {
        return _usedProofs[proofHash];
    }

    /**
     * @dev Updates the authorized oracle address
     * @param newOracle New oracle contract address
     */
    function updateOracle(address newOracle) external onlyOwner {
        require(newOracle != address(0), "MikoToken: new oracle is zero address");
        address oldOracle = oracle;
        oracle = newOracle;
        emit OracleUpdated(oldOracle, newOracle);
    }

    // ==================== Internal Functions ====================

    function _transfer(address from, address to, uint256 amount) internal {
        require(from != address(0), "MikoToken: transfer from zero address");
        require(to != address(0), "MikoToken: transfer to zero address");
        require(_balances[from] >= amount, "MikoToken: transfer amount exceeds balance");

        _balances[from] -= amount;
        _balances[to] += amount;
        emit Transfer(from, to, amount);
    }

    function _approve(address _owner, address spender, uint256 amount) internal {
        require(_owner != address(0), "MikoToken: approve from zero address");
        require(spender != address(0), "MikoToken: approve to zero address");

        _allowances[_owner][spender] = amount;
        emit Approval(_owner, spender, amount);
    }
}
