from simulator.strategy import Strategy
from simulator.blockchain import Block

from simulator.strategy import Strategy
from simulator.blockchain import Block

class MaStratEmmyKa(Strategy):
    """
    Stratégie du meillleur groupe.
    We <3 blockchain
    """

    def __init__(self, node_id: str):
        super().__init__(node_id)

        self.blocks_seen = set()
        self.last_block_receive_tick = -100
        self.safe_mining_interval = 5

    def on_block_received(self, block: Block, sender_id: str) -> bool:
        """Decide si on relaye ce bloc aux autres"""

        if block.hash in self.blocks_seen:
            return False
        
        self.blocks_seen.add(block.hash)

        assert self.blockchain is not None
        added = self.blockchain.add_block(block)

        if not added:
            return False

        if block.parent_hash == self.blockchain.get_head().parent.hash:
            return True
        
        if self.blockchain.has_fork():
            return True

        return True  # relayer toujours si autre cas
    


    def should_mine_block(self) -> bool:
        """Decide si on cree un bloc ce tick (1000 ticks total)"""

        if self.current_tick - self.last_block_receive_tick < self.safe_mining_interval:
            return False
        
        # si y'a fork -> on aggrave pas
        if self.has_fork():
            return False
        
        return self.current_tick % 3 == 0
        
    
    
    
    def choose_parent_block(self) -> str:
        """Choisit le parent du nouveau bloc"""
        
        assert self.blockchain is not None

        tips = self.blockchain.get_all_tips()

        max_height = max(tip.height for tip in tips)

        bests = [tip for tip in tips if tip.height == max_height]

        best = min(bests, key = lambda b: b.timestamp)

        return best.hash  
    
