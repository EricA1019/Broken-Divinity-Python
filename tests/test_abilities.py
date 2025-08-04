"""
Tests for the ability system.

Tests ability loading, validation, and registry functionality following
the "public API only" testing approach.

Author: GitHub Copilot
"""

import pytest
import tempfile
import json
import os
from pathlib import Path

from src.game.abilities import (
    Ability, AbilityCost, AbilityEffects, AbilityRegistry,
    get_ability_registry, setup_ability_registry
)
from src.core.signals import get_signal_bus, CoreSignal


class TestAbilityCost:
    """Test ability cost functionality."""
    
    def test_basic_cost_creation(self):
        """Test creating basic ability costs."""
        cost = AbilityCost(ammo=2, mana=1)
        assert cost.ammo == 2
        assert cost.mana == 1
        assert cost.health == 0
    
    def test_can_afford_sufficient_resources(self):
        """Test resource checking with sufficient resources."""
        cost = AbilityCost(ammo=2, mana=1)
        assert cost.can_afford(current_ammo=5, current_mana=3, current_health=10)
    
    def test_can_afford_insufficient_resources(self):
        """Test resource checking with insufficient resources."""
        cost = AbilityCost(ammo=5, mana=3)
        assert not cost.can_afford(current_ammo=2, current_mana=1, current_health=10)
    
    def test_apply_cost(self):
        """Test applying ability costs."""
        cost = AbilityCost(ammo=2, mana=1, health=1)
        new_ammo, new_mana, new_health = cost.apply_cost(10, 5, 20)
        assert new_ammo == 8
        assert new_mana == 4
        assert new_health == 19


class TestAbilityEffects:
    """Test ability effects functionality."""
    
    def test_damage_effects(self):
        """Test damage effect properties."""
        effects = AbilityEffects(base_damage=[2, 6], accuracy_modifier=1)
        assert effects.get_damage_range() == (2, 6)
        assert effects.accuracy_modifier == 1
    
    def test_heal_effects(self):
        """Test healing effect properties."""
        effects = AbilityEffects(heal_amount=[5, 10], removes_bleeding=True)
        assert effects.get_heal_range() == (5, 10)
        assert effects.removes_bleeding is True
    
    def test_defense_effects(self):
        """Test defensive effect properties."""
        effects = AbilityEffects(defense_bonus=3, duration=2)
        assert effects.defense_bonus == 3
        assert effects.duration == 2


class TestAbility:
    """Test core ability functionality."""
    
    def test_create_attack_ability(self):
        """Test creating an attack ability."""
        cost = AbilityCost(ammo=1)
        effects = AbilityEffects(base_damage=[3, 5])
        
        ability = Ability(
            id="test_shot",
            name="Test Shot",
            description="A test attack",
            type="attack",
            damage_type="ballistic",
            cost=cost,
            cooldown=0,
            range=3,
            targeting="single",
            effects=effects
        )
        
        assert ability.is_attack_ability()
        assert not ability.is_heal_ability()
        assert ability.get_damage_range() == (3, 5)
    
    def test_create_heal_ability(self):
        """Test creating a healing ability."""
        cost = AbilityCost(mana=2)
        effects = AbilityEffects(heal_amount=[8, 12])
        
        ability = Ability(
            id="test_heal",
            name="Test Heal",
            description="A test heal",
            type="heal",
            damage_type="none",
            cost=cost,
            cooldown=3,
            range=1,
            targeting="self_or_ally",
            effects=effects
        )
        
        assert ability.is_heal_ability()
        assert not ability.is_attack_ability()
        assert ability.can_target_allies()
        assert ability.get_heal_range() == (8, 12)
    
    def test_self_targeting_ability(self):
        """Test self-targeting ability properties."""
        cost = AbilityCost()
        effects = AbilityEffects(defense_bonus=2)
        
        ability = Ability(
            id="test_defense",
            name="Test Defense",
            description="A test defense",
            type="defense",
            damage_type="none",
            cost=cost,
            cooldown=1,
            range=0,
            targeting="self",
            effects=effects
        )
        
        assert ability.is_self_targeting()
        assert not ability.can_target_allies()


class TestAbilityRegistry:
    """Test ability registry functionality."""
    
    def test_registry_initialization(self):
        """Test registry creates properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            registry = AbilityRegistry(Path(temp_dir))
            assert registry.get_item_count() == 0
    
    def test_load_detective_abilities(self):
        """Test loading detective abilities from JSON."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test abilities file
            abilities_data = {
                "detective_abilities": [
                    {
                        "id": "test_shot",
                        "name": "Test Shot",
                        "description": "A test shot",
                        "type": "attack",
                        "damage_type": "ballistic",
                        "cost": {"ammo": 1, "mana": 0},
                        "cooldown": 0,
                        "range": 3,
                        "targeting": "single",
                        "effects": {"base_damage": [2, 4]}
                    }
                ]
            }
            
            file_path = os.path.join(temp_dir, "test_abilities.json")
            with open(file_path, 'w') as f:
                json.dump(abilities_data, f)
            
            registry = AbilityRegistry(Path(temp_dir))
            registry.load_data()
            
            assert registry.get_item_count() == 1
            ability = registry.get_item("test_shot")
            assert ability is not None
            assert ability.name == "Test Shot"
            assert ability.cost.ammo == 1
    
    def test_load_multiple_ability_types(self):
        """Test loading different types of abilities."""
        with tempfile.TemporaryDirectory() as temp_dir:
            abilities_data = {
                "detective_abilities": [
                    {
                        "id": "attack_ability",
                        "name": "Attack",
                        "description": "Attack ability",
                        "type": "attack",
                        "damage_type": "ballistic",
                        "cost": {"ammo": 1},
                        "cooldown": 0,
                        "range": 3,
                        "targeting": "single",
                        "effects": {"base_damage": [2, 4]}
                    },
                    {
                        "id": "heal_ability",
                        "name": "Heal",
                        "description": "Heal ability",
                        "type": "heal",
                        "damage_type": "none",
                        "cost": {"mana": 2},
                        "cooldown": 3,
                        "range": 1,
                        "targeting": "self",
                        "effects": {"heal_amount": [5, 8]}
                    }
                ]
            }
            
            file_path = os.path.join(temp_dir, "abilities.json")
            with open(file_path, 'w') as f:
                json.dump(abilities_data, f)
            
            registry = AbilityRegistry(Path(temp_dir))
            registry.load_data()
            
            assert registry.get_item_count() == 2
            
            # Test type filtering
            attack_abilities = registry.get_attack_abilities()
            heal_abilities = registry.get_heal_abilities()
            
            assert len(attack_abilities) == 1
            assert len(heal_abilities) == 1
            assert attack_abilities[0].id == "attack_ability"
            assert heal_abilities[0].id == "heal_ability"
    
    def test_ability_validation(self):
        """Test ability validation during loading."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid ability (missing required fields)
            invalid_data = {
                "detective_abilities": [
                    {
                        "id": "",  # Invalid empty ID
                        "name": "Invalid Ability",
                        "type": "attack"
                        # Missing other required fields
                    }
                ]
            }
            
            file_path = os.path.join(temp_dir, "invalid.json")
            with open(file_path, 'w') as f:
                json.dump(invalid_data, f)
            
            registry = AbilityRegistry(Path(temp_dir))
            registry.load_data()
            
            # Should not load invalid abilities
            assert registry.get_item_count() == 0
    
    def test_get_abilities_for_entity(self):
        """Test getting abilities for specific entities."""
        with tempfile.TemporaryDirectory() as temp_dir:
            abilities_data = {
                "detective_abilities": [
                    {
                        "id": "detective_shot",
                        "name": "Detective Shot",
                        "description": "Detective attack",
                        "type": "attack",
                        "damage_type": "ballistic",
                        "cost": {"ammo": 1},
                        "cooldown": 0,
                        "range": 3,
                        "targeting": "single",
                        "effects": {"base_damage": [2, 4]}
                    }
                ]
            }
            
            file_path = os.path.join(temp_dir, "abilities.json")
            with open(file_path, 'w') as f:
                json.dump(abilities_data, f)
            
            registry = AbilityRegistry(Path(temp_dir))
            registry.load_data()
            
            # For now, all entities get all abilities
            detective_abilities = registry.get_abilities_for_entity("detective")
            assert len(detective_abilities) == 1
            assert detective_abilities[0].id == "detective_shot"


class TestAbilityRegistryIntegration:
    """Test ability registry integration with signal system."""
    
    def test_registry_signals(self):
        """Test that registry emits proper signals."""
        signal_bus = get_signal_bus()
        received_signals = []
        
        def signal_listener(signal_data):
            received_signals.append(signal_data)
        
        signal_bus.listen(CoreSignal.REGISTRY_INITIALIZED, signal_listener)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            abilities_data = {
                "detective_abilities": [
                    {
                        "id": "test_ability",
                        "name": "Test",
                        "description": "Test ability",
                        "type": "attack",
                        "damage_type": "ballistic",
                        "cost": {"ammo": 1},
                        "cooldown": 0,
                        "range": 1,
                        "targeting": "single",
                        "effects": {"base_damage": [1, 2]}
                    }
                ]
            }
            
            file_path = os.path.join(temp_dir, "test.json")
            with open(file_path, 'w') as f:
                json.dump(abilities_data, f)
            
            # Setup registry (should emit signal)
            setup_ability_registry(Path(temp_dir))
            
            # Check signal was emitted
            registry_signals = [s for s in received_signals if s.source == "AbilityRegistry"]
            assert len(registry_signals) >= 1
            assert registry_signals[0].data["registry_name"] == "abilities"
            assert registry_signals[0].data["item_count"] == 1
    
    def test_global_registry_access(self):
        """Test global registry access function."""
        # Clear any existing registry
        import src.game.abilities
        src.game.abilities._ability_registry = None
        
        # Create test data
        with tempfile.TemporaryDirectory() as temp_dir:
            abilities_data = {
                "detective_abilities": [
                    {
                        "id": "global_test",
                        "name": "Global Test",
                        "description": "Global test ability",
                        "type": "attack",
                        "damage_type": "ballistic",
                        "cost": {"ammo": 1},
                        "cooldown": 0,
                        "range": 1,
                        "targeting": "single",
                        "effects": {"base_damage": [1, 2]}
                    }
                ]
            }
            
            file_path = os.path.join(temp_dir, "global_test.json")
            with open(file_path, 'w') as f:
                json.dump(abilities_data, f)
            
            # Setup global registry
            setup_ability_registry(Path(temp_dir))
            
            # Access through global function
            registry = get_ability_registry()
            assert registry.get_item_count() == 1
            assert registry.has_item("global_test")


if __name__ == "__main__":
    # Simple test runner when executed directly
    print("🧪 Running Ability System Tests...")
    
    # Test ability cost
    cost = AbilityCost(ammo=2, mana=1)
    print(f"✅ AbilityCost: {cost.ammo} ammo, {cost.mana} mana")
    
    # Test ability effects
    effects = AbilityEffects(base_damage=[3, 6], accuracy_modifier=1)
    print(f"✅ AbilityEffects: {effects.get_damage_range()} damage")
    
    # Test ability creation
    ability = Ability(
        id="test_shot", name="Test Shot", description="Test",
        type="attack", damage_type="ballistic", cost=cost,
        cooldown=0, range=3, targeting="single", effects=effects
    )
    print(f"✅ Ability: {ability.name} ({ability.get_damage_range()} damage)")
    
    print("🎯 Ability system basic functionality verified!")
