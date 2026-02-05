from simulator.strategy import Strategy
from simulator.blockchain import Block

class MaStrategie(Strategy):
    def __init__(self, node_id: str):
        super().__init__(node_id)
        
        # Paramètres adaptatifs
        self.base_mining_frequency = 10
        self.current_mining_frequency = 1
        
        # Historique des forks observés
        self.fork_history = []
        self.observation_window = 20
        
        self.blocks_seen = set()

    def _adapt_parameters(self):
        """Adapte les paramètres selon les observations."""
        if not self.fork_history:
            return
        
        fork_rate = sum(self.fork_history) / len(self.fork_history)
        
        if fork_rate > 0.5:
            self.current_mining_frequency = int(self.base_mining_frequency * 0.5)
        elif fork_rate < 0.2:
            self.current_mining_frequency = max(5, int(self.base_mining_frequency * 1.8))
        else:
            # Normal
            self.current_mining_frequency = self.base_mining_frequency
    
    def should_mine_block(self) -> bool:
        """Decide si on cree un bloc ce tick (1000 ticks total)"""
        return self.current_tick % self.current_mining_frequency == 0

    def on_block_received(self, block: Block, sender_id: str) -> bool:
        """Reçoit et analyse les blocs."""
        if block.hash in self.blocks_seen:
            return False
        
        self.blocks_seen.add(block.hash)
        assert self.blockchain is not None
        added = self.blockchain.add_block(block)
        
        # Observer si on a des forks
        has_fork = self.blockchain.has_fork()
        self.fork_history.append(has_fork)
        
        # Garder une fenêtre glissante
        if len(self.fork_history) > self.observation_window:
            self.fork_history.pop(0)
        
        # Adapter le comportement
        self._adapt_parameters()
        
        if added:
            return True
        
        return False
    
    def choose_parent_block(self) -> str:
        """Choisit intelligemment en cas de fork."""
        assert self.blockchain is not None
        tips = self.blockchain.get_all_tips()
        
        if len(tips) == 1:
            # Pas de fork, simple
            return tips[0].hash
        
        # En cas de fork, choisir le tip avec la plus grande hauteur
        best_tip = max(tips, key=lambda b: b.height)
        return best_tip.hash