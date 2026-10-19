import unittest
from pathlib import Path

class TestMilestone1ImmersiveSkills(unittest.TestCase):
    def test_immersive_skills_exist(self):
        skill_names = [
            'cinematic-scroll-experience',
            'advanced-3d-interface-design',
            'advanced-motion-design',
            'immersive-ui-composition'
        ]
        for name in skill_names:
            p1 = Path(f'.agents/skills/{name}/SKILL.md')
            p2 = Path(f'hermes-agent/skills/software-development/{name}/SKILL.md')
            self.assertTrue(p1.exists(), f'.agents skill {name} should exist')
            self.assertTrue(p2.exists(), f'hermes-agent skill {name} should exist')
            
            content = p1.read_text(encoding='utf-8')
            self.assertIn(f'name: {name}', content)

if __name__ == '__main__':
    unittest.main()
