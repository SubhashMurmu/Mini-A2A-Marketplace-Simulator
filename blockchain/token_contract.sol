// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract A2AToken {
    string public name = "A2A Marketplace Token";
    string public symbol = "A2A";
    uint8 public decimals = 18;
    uint256 public totalSupply;
    
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    // Service payment tracking
    mapping(bytes32 => ServicePayment) public servicePayments;
    
    struct ServicePayment {
        address client;
        address provider;
        uint256 amount;
        string serviceType;
        bool completed;
        uint256 timestamp;
    }
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event ServicePaid(bytes32 indexed paymentId, address indexed client, 
                     address indexed provider, uint256 amount, string serviceType);
    event ServiceCompleted(bytes32 indexed paymentId);
    
    constructor(uint256 _initialSupply) {
        totalSupply = _initialSupply * 10 ** decimals;
        balanceOf[msg.sender] = totalSupply;
    }
    
    function transfer(address _to, uint256 _value) public returns (bool) {
        require(balanceOf[msg.sender] >= _value, "Insufficient balance");
        require(_to != address(0), "Invalid address");
        
        balanceOf[msg.sender] -= _value;
        balanceOf[_to] += _value;
        
        emit Transfer(msg.sender, _to, _value);
        return true;
    }
    
    function approve(address _spender, uint256 _value) public returns (bool) {
        allowance[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }
    
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool) {
        require(balanceOf[_from] >= _value, "Insufficient balance");
        require(allowance[_from][msg.sender] >= _value, "Insufficient allowance");
        require(_to != address(0), "Invalid address");
        
        balanceOf[_from] -= _value;
        balanceOf[_to] += _value;
        allowance[_from][msg.sender] -= _value;
        
        emit Transfer(_from, _to, _value);
        return true;
    }
    
    function payForService(address _provider, uint256 _amount, 
                          string memory _serviceType) public returns (bytes32) {
        require(balanceOf[msg.sender] >= _amount, "Insufficient balance");
        require(_provider != address(0), "Invalid provider address");
        
        bytes32 paymentId = keccak256(abi.encodePacked(
            msg.sender, _provider, _amount, _serviceType, block.timestamp
        ));
        
        // Hold funds in escrow
        balanceOf[msg.sender] -= _amount;
        
        servicePayments[paymentId] = ServicePayment({
            client: msg.sender,
            provider: _provider,
            amount: _amount,
            serviceType: _serviceType,
            completed: false,
            timestamp: block.timestamp
        });
        
        emit ServicePaid(paymentId, msg.sender, _provider, _amount, _serviceType);
        return paymentId;
    }
    
    function completeService(bytes32 _paymentId) public {
        ServicePayment storage payment = servicePayments[_paymentId];
        require(payment.provider == msg.sender, "Only provider can complete");
        require(!payment.completed, "Already completed");
        
        payment.completed = true;
        balanceOf[payment.provider] += payment.amount;
        
        emit ServiceCompleted(_paymentId);
        emit Transfer(address(this), payment.provider, payment.amount);
    }
    
    function refundService(bytes32 _paymentId) public {
        ServicePayment storage payment = servicePayments[_paymentId];
        require(payment.client == msg.sender, "Only client can request refund");
        require(!payment.completed, "Service already completed");
        require(block.timestamp > payment.timestamp + 1 hours, "Too early for refund");
        
        payment.completed = true; // Mark as resolved
        balanceOf[payment.client] += payment.amount;
        
        emit Transfer(address(this), payment.client, payment.amount);
    }
}