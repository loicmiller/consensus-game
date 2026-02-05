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
    
    def should_mine_block(self) -> bool:
        """Decide si on cree un bloc ce tick (1000 ticks total)"""
        return True
   
    def on_block_received(self, block: Block, sender_id: str) -> bool:
        """Decide si on relaye ce bloc aux autres"""
        if block.hash in self.blocks_seen:
            return False
        
        self.blocks_seen.add(block.hash)
        
        # Enregistrer le moment de réception
        self.pending_blocks[block.hash] = self.current_tick
        
        # Ajouter à la blockchain
        assert self.blockchain is not None
        self.blockchain.add_block(block)
        
        # Relayer seulement après le délai d'attente
        ticks_waiting = self.current_tick - self.pending_blocks.get(block.hash, 0)
        
        if ticks_waiting >= self.wait_time:
            return True
        
        return False
    
    def choose_parent_block(self) -> str:
        """Choisit le parent du nouveau bloc"""
        assert self.blockchain is not None
        return self.blockchain.get_head().hash