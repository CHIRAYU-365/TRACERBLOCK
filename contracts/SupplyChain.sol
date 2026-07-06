// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SupplyChain {
    address public admin;

    struct Product {
        uint256 id;
        address currentOwner;
        string status;
        string location;
        bool isRecalled;
    }

    struct TrackingEvent {
        uint256 productId;
        address updatedBy;
        string status;
        string location;
        uint256 temperature;
        uint256 timestamp;
    }
    
    mapping(uint256 => Product) public products;
    mapping(uint256 => TrackingEvent[]) public productEvents;
    
    event ProductRegistered(uint256 indexed productId, address owner);
    event OwnershipTransferred(uint256 indexed productId, address from, address to);
    event EventLogged(uint256 indexed productId, string status, string location, uint256 temp, uint256 timestamp);
    event RecallAlert(uint256 indexed productId, string reason);

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not authorized");
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    function registerProduct(uint256 _productId, string memory _initialStatus, string memory _location) public {
        require(products[_productId].currentOwner == address(0), "Product already exists");
        products[_productId] = Product(_productId, msg.sender, _initialStatus, _location, false);
        emit ProductRegistered(_productId, msg.sender);
    }
    
    function logEvent(uint256 _productId, string memory _status, string memory _location, uint256 _temperature) public {
        require(products[_productId].currentOwner != address(0), "Product not found");
        require(!products[_productId].isRecalled, "Product is recalled");

        TrackingEvent memory newEvent = TrackingEvent({
            productId: _productId,
            updatedBy: msg.sender,
            status: _status,
            location: _location,
            temperature: _temperature,
            timestamp: block.timestamp
        });
        
        productEvents[_productId].push(newEvent);
        products[_productId].status = _status;
        products[_productId].location = _location;

        emit EventLogged(_productId, _status, _location, _temperature, block.timestamp);

        // Simple condition monitoring
        if (_temperature > 30 || _temperature < 2) {
            products[_productId].isRecalled = true;
            emit RecallAlert(_productId, "Temperature out of safe bounds (2C - 30C)");
        }
    }

    function transferOwnership(uint256 _productId, address _newOwner) public {
        require(products[_productId].currentOwner == msg.sender, "Only current owner can transfer");
        require(!products[_productId].isRecalled, "Cannot transfer recalled product");
        
        address previousOwner = products[_productId].currentOwner;
        products[_productId].currentOwner = _newOwner;
        
        emit OwnershipTransferred(_productId, previousOwner, _newOwner);
    }
    
    function getEventCount(uint256 _productId) public view returns (uint256) {
        return productEvents[_productId].length;
    }
}
