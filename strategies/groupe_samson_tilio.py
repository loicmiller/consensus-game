"""
Stratégie gourmande : mine le plus rapidement possible.

Comportement:
- Mine à chaque opportunité
- Relaie immédiatement tous les blocs
- Suit toujours la chaîne la plus longue



Avantages:
- Produit beaucoup de blocs
- Réagit rapidement

Inconvénients:
- Peut créer beaucoup de forks
- Peut être moins stable
"""
from simulator.strategy import Strategy
from simulator.blockchain import Block


class SamTilStra(Strategy):
    """Stratégie de minage agressif."""

    def __init__(self, node_id: str):
        super().__init__(node_id)
        
        # Temps d'attente avant de relayer (en ticks)
        self.wait_time = 15
        
        # Fréquence de minage
        self.mining_frequency = 20
        
        # Blocs en attente : {block_hash: tick_received}
        self.pending_blocks = {}
        
        self.blocks_seen = set()
    
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
    
    def should_mine_block(self) -> bool:
        """Mine à chaque tick !"""
        return True
    
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