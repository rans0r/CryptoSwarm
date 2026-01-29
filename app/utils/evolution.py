"""
Evolutionary swarm algorithm for optimizing trading bots.
"""
from typing import List, Tuple
import random
from sqlalchemy.orm import Session
from app.models.models import Bot, SwarmPool
from app.utils.ai_interpreter import ai_interpreter
from config import settings


class SwarmEvolution:
    """Manages evolutionary algorithms for bot swarms."""
    
    def __init__(self, db: Session):
        """Initialize swarm evolution manager."""
        self.db = db
    
    def calculate_fitness(self, bot: Bot) -> float:
        """
        Calculate fitness score for a bot based on its performance.
        
        Args:
            bot: Bot instance
            
        Returns:
            Fitness score (higher is better)
        """
        # Base fitness on profit/loss with penalties for trades and fees
        if bot.total_trades == 0:
            return 0.0
        
        # Calculate win rate
        win_rate = bot.winning_trades / bot.total_trades if bot.total_trades > 0 else 0
        
        # Calculate average profit per trade
        avg_profit = bot.total_profit_loss / bot.total_trades if bot.total_trades > 0 else 0
        
        # Fitness function combines multiple factors
        fitness = (
            bot.total_profit_loss * 1.0 +  # Absolute profit
            win_rate * 100 +                # Win rate bonus
            avg_profit * 10                 # Reward consistent profits
        )
        
        return fitness
    
    def select_parents(
        self, 
        pool: SwarmPool, 
        bots: List[Bot], 
        num_parents: int = 2
    ) -> List[Bot]:
        """
        Select parent bots for reproduction using tournament selection.
        
        Args:
            pool: Swarm pool
            bots: List of active bots in the pool
            num_parents: Number of parents to select
            
        Returns:
            List of selected parent bots
        """
        if len(bots) < num_parents:
            return bots
        
        # Update fitness scores
        for bot in bots:
            bot.fitness_score = self.calculate_fitness(bot)
        
        # Tournament selection
        parents = []
        for _ in range(num_parents):
            # Randomly select tournament candidates
            tournament_size = min(5, len(bots))
            tournament = random.sample(bots, tournament_size)
            
            # Select best from tournament
            winner = max(tournament, key=lambda b: b.fitness_score)
            parents.append(winner)
        
        return parents
    
    async def mutate_bot(self, bot: Bot) -> Bot:
        """
        Create a mutated version of a bot.
        
        Args:
            bot: Parent bot
            
        Returns:
            New mutated bot
        """
        # Generate mutated rule using AI
        mutated_rule = await ai_interpreter.generate_mutation(
            bot.natural_language_rule,
            mutation_type="random"
        )
        
        # Interpret the new rule
        interpreted_rule = await ai_interpreter.interpret_rule(mutated_rule)
        
        # Create new bot with mutation
        new_bot = Bot(
            name=f"{bot.name}_mut{bot.mutation_count + 1}",
            description=f"Mutation of {bot.name}",
            natural_language_rule=mutated_rule,
            interpreted_rule=interpreted_rule,
            is_active=True,
            generation=bot.generation + 1,
            parent_id=bot.id,
            mutation_count=bot.mutation_count + 1
        )
        
        return new_bot
    
    async def crossover_bots(self, parent1: Bot, parent2: Bot) -> Bot:
        """
        Create a child bot by crossing over two parent bots.
        
        Args:
            parent1: First parent bot
            parent2: Second parent bot
            
        Returns:
            New child bot with combined traits
        """
        # Generate crossover rule using AI
        crossover_rule = await ai_interpreter.crossover_rules(
            parent1.natural_language_rule,
            parent2.natural_language_rule
        )
        
        # Interpret the new rule
        interpreted_rule = await ai_interpreter.interpret_rule(crossover_rule)
        
        # Create new bot with crossover
        new_bot = Bot(
            name=f"{parent1.name}_x_{parent2.name}",
            description=f"Crossover of {parent1.name} and {parent2.name}",
            natural_language_rule=crossover_rule,
            interpreted_rule=interpreted_rule,
            is_active=True,
            generation=max(parent1.generation, parent2.generation) + 1,
            parent_id=parent1.id
        )
        
        return new_bot
    
    async def evolve_pool(self, pool: SwarmPool) -> dict:
        """
        Evolve a swarm pool by selection, crossover, and mutation.
        
        Args:
            pool: Swarm pool to evolve
            
        Returns:
            Evolution statistics dictionary
        """
        if not settings.enable_evolution:
            return {"status": "Evolution disabled in settings"}
        
        # Get all active bots in the pool
        all_bots = self.db.query(Bot).filter(Bot.is_active == True).all()
        
        if len(all_bots) < 2:
            return {"status": "Not enough bots for evolution", "bot_count": len(all_bots)}
        
        # Calculate fitness for all bots
        for bot in all_bots:
            bot.fitness_score = self.calculate_fitness(bot)
        
        # Sort by fitness
        all_bots.sort(key=lambda b: b.fitness_score, reverse=True)
        
        # Determine selection cutoff
        keep_count = max(2, int(len(all_bots) * pool.selection_pressure))
        survivors = all_bots[:keep_count]
        eliminated = all_bots[keep_count:]
        
        # Deactivate eliminated bots
        for bot in eliminated:
            bot.is_active = False
        
        # Generate new bots through mutation and crossover
        new_bots = []
        
        # Mutations
        if random.random() < settings.mutation_rate:
            parent = random.choice(survivors)
            mutated = await self.mutate_bot(parent)
            new_bots.append(mutated)
        
        # Crossovers
        if random.random() < settings.crossover_rate and len(survivors) >= 2:
            parents = random.sample(survivors, 2)
            child = await self.crossover_bots(parents[0], parents[1])
            new_bots.append(child)
        
        # Add new bots to database
        for bot in new_bots:
            self.db.add(bot)
        
        # Update pool statistics
        if survivors:
            pool.best_fitness = survivors[0].fitness_score
        
        self.db.commit()
        
        return {
            "status": "Evolution completed",
            "survivors": len(survivors),
            "eliminated": len(eliminated),
            "new_bots": len(new_bots),
            "best_fitness": pool.best_fitness
        }
