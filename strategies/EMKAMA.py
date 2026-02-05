from simulator.strategy import Strategy
from simulator.blockchain import Block

class Merge(Strategy):

    def __init__(self, node_id: str):
            super().__init__(node_id)

            self.current_tick = 0
            self.blocks_mined = 0
            self.blocks_received = 0
            self.seen_blocks = set()
            #self.strategy_mode = "honest"
            self.mine_probability = 1.0  # 1.0 = toujours miner
    
    def should_mine_block(self) -> bool:
        """Décide s'il faut miner."""
        if self.current_tick - self.last_mine_tick >= self.mining_frequency:
            self.last_mine_tick = self.current_tick
            self.log(f"Tentative de minage au tick {self.current_tick}")
            return True
        return False
    
    def on_block_received(self, block: Block, sender_id: str) -> bool:
        """Attend avant de relayer."""
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
        """Choisit intelligemment en cas de fork."""
        assert self.blockchain is not None
        tips = self.blockchain.get_all_tips()
        
        if len(tips) == 1:
            # Pas de fork, simple
            return tips[0].hash
        
        # En cas de fork, choisir le tip avec la plus grande hauteur
        best_tip = max(tips, key=lambda b: b.height)
        return best_tip.hash