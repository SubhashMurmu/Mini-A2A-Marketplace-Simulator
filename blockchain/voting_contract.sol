// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AgentReputation {
    struct Agent {
        string name;
        uint256 totalRating;
        uint256 ratingCount;
        bool registered;
    }
    
    mapping(address => Agent) public agents;
    mapping(address => mapping(address => bool)) public hasRated;
    
    event AgentRegistered(address indexed agent, string name);
    event AgentRated(address indexed agent, address indexed rater, uint8 rating);
    
    function registerAgent(string memory _name) public {
        require(!agents[msg.sender].registered, "Agent already registered");
        
        agents[msg.sender] = Agent({
            name: _name,
            totalRating: 0,
            ratingCount: 0,
            registered: true
        });
        
        emit AgentRegistered(msg.sender, _name);
    }
    
    function rateAgent(address _agent, uint8 _rating) public {
        require(agents[_agent].registered, "Agent not registered");
        require(_rating >= 1 && _rating <= 5, "Rating must be 1-5");
        require(!hasRated[_agent][msg.sender], "Already rated this agent");
        require(_agent != msg.sender, "Cannot rate yourself");
        
        agents[_agent].totalRating += _rating;
        agents[_agent].ratingCount += 1;
        hasRated[_agent][msg.sender] = true;
        
        emit AgentRated(_agent, msg.sender, _rating);
    }
    
    function getAgentRating(address _agent) public view returns (uint256, uint256) {
        Agent memory agent = agents[_agent];
        if (agent.ratingCount == 0) {
            return (0, 0);
        }
        return (agent.totalRating, agent.ratingCount);
    }
    
    function getAverageRating(address _agent) public view returns (uint256) {
        Agent memory agent = agents[_agent];
        if (agent.ratingCount == 0) {
            return 0;
        }
        return (agent.totalRating * 100) / agent.ratingCount; // Multiply by 100 for precision
    }
}