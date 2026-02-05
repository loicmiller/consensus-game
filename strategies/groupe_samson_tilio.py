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


class GreedyMiner(Strategy):
    """Stratégie de minage agressif."""
    
    def __init__(self, node_id: str):
        super().__init__(node_id)
        self.blocks_seen = set()
    
    def on_block_received(self, block: Block, sender_id: str) -> bool:
        """Accepte et relaie immédiatement tous les blocs."""
        if block.hash in self.blocks_seen:
            return False
        
        self.blocks_seen.add(block.hash)
        assert self.blockchain is not None
        added = self.blockchain.add_block(block)
        
        if added:
            return True
        
        return False
    
    def should_mine_block(self) -> bool:
        """Mine à chaque tick !"""
        return True
    
    def choose_parent_block(self) -> str:
        """Toujours la chaîne la plus longue."""
        assert self.blockchain is not None
        return self.blockchain.get_head().hash