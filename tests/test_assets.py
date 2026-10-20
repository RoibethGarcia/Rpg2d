"""Contracts for the small, redistributable resource selection."""
import hashlib
import json
import os
from pathlib import Path
import unittest

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

ROOT = Path(__file__).resolve().parents[1]


class AssetTests(unittest.TestCase):
    def manifest(self):
        path = ROOT / "assets/manifest.json"
        self.assertTrue(path.is_file(), "The asset manifest must be supplied")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_required_roles_and_provenance_are_explicit(self):
        manifest = self.manifest()
        self.assertEqual(manifest["version"], 1)
        self.assertTrue({"human_front", "human_rear", "pipes"} <= manifest["images"].keys())
        self.assertTrue({"click", "confirm", "error", "back"} <= manifest["sounds"].keys())
        for group in ("images", "sounds"):
            for entry in manifest[group].values():
                with self.subTest(path=entry["path"]):
                    if entry.get('source_type') in ('user_supplied', 'ai_generated'):
                        self.assertEqual(group, 'images')
                        self.assertEqual(entry['redistribution_status'], 'pending_confirmation')
                        self.assertNotIn('license', entry)
                        self.assertNotIn('license_file', entry)
                        provenance = (ROOT / entry['provenance_file']).resolve()
                        self.assertTrue(provenance.is_relative_to(ROOT / 'assets/provenance'))
                        self.assertTrue(provenance.is_file())
                        if entry['source_type'] == 'ai_generated':
                            prompt = (ROOT / entry['prompt_file']).resolve()
                            self.assertTrue(prompt.is_relative_to(ROOT / 'assets/provenance'))
                            self.assertTrue(prompt.is_file())
                            self.assertTrue(entry['references'])
                            for reference in entry['references']:
                                ref = (ROOT / reference['path']).resolve()
                                self.assertTrue(ref.is_relative_to(ROOT / 'assets/reference/scenarios'))
                                self.assertTrue(ref.is_file())
                                self.assertEqual(reference['source_type'], 'user_supplied')
                                self.assertEqual(hashlib.sha256(ref.read_bytes()).hexdigest(), reference['sha256'])
                    else:
                        self.assertIn(entry["license"], {"CC0-1.0", "CC-BY-SA-4.0"})
                        self.assertTrue(entry["source"].startswith("https://"))
                        self.assertTrue((ROOT / entry["license_file"]).is_file())
                    self.assertTrue(entry['source'])
                    self.assertTrue(entry["author"])
                    self.assertTrue(entry["original_path"])
                    path = (ROOT / entry["path"]).resolve()
                    self.assertTrue(path.is_relative_to(ROOT / "assets"))
                    self.assertTrue(path.is_file())
                    self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry["sha256"])

    def test_images_match_declared_size_transparency_and_frames(self):
        for name, entry in self.manifest()["images"].items():
            with self.subTest(name=name):
                image = pygame.image.load(str(ROOT / entry["path"]))
                self.assertEqual(list(image.get_size()), entry["size"])
                if entry.get('background') == 'opaque_black':
                    self.assertIn(name, ('hondonada_plate', 'puesto_plate', 'planta_plate'))
                    self.assertEqual(entry['usage'], 'layered_environment_plate')
                    self.assertLessEqual(max(tuple(image.get_at((0, 0)))[:3]), 4)
                    self.assertTrue(all(pixel.a == 255 for pixel in (
                        image.get_at((0, 0)), image.get_at((image.get_width() // 2, image.get_height() // 2)))))
                else:
                    self.assertTrue(image.get_colorkey() is not None or image.get_masks()[3])
                frame = pygame.Rect(entry.get("frame", [0, 0, *entry["size"]]))
                self.assertTrue(image.get_rect().contains(frame))
                self.assertTrue(0 <= entry["anchor"][0] <= frame.width)
                self.assertTrue(0 <= entry["anchor"][1] <= frame.height)

    def test_audio_decodes_without_requiring_real_audio_device(self):
        pygame.mixer.init()
        try:
            for name, entry in self.manifest()["sounds"].items():
                with self.subTest(name=name):
                    sound = pygame.mixer.Sound(str(ROOT / entry["path"]))
                    self.assertGreater(sound.get_length(), 0)
                    self.assertAlmostEqual(sound.get_length(), entry["duration_seconds"], places=2)
        finally:
            pygame.mixer.quit()

    def test_hondonada_clean_plate_is_registered_with_exact_source_and_prompt(self):
        images = self.manifest()['images']
        self.assertIn('hondonada_plate', images)
        plate = images['hondonada_plate']
        self.assertEqual(plate['path'], 'assets/images/environments/hondonada_clean.png')
        self.assertEqual(plate['source_type'], 'ai_generated')
        self.assertEqual(plate['usage'], 'layered_environment_plate')
        self.assertEqual(plate['background'], 'opaque_black')
        self.assertEqual([ref['path'] for ref in plate['references']],
                         ['assets/reference/scenarios/hondonada.png'])
        prompt = (ROOT / plate['prompt_file']).read_text(encoding='utf-8')
        self.assertIn('Remove ONLY the small human protagonist', prompt)
        self.assertIn('Pixel registered layout is critically important', prompt)

    def test_puesto_clean_plate_is_registered_with_source_hash_and_prompt(self):
        plate = self.manifest()['images']['puesto_plate']
        self.assertEqual(plate['path'], 'assets/images/environments/puesto-clean.png')
        self.assertEqual(plate['size'], [1448,1086])
        self.assertEqual(plate['source_type'], 'ai_generated')
        self.assertEqual(plate['usage'], 'layered_environment_plate')
        self.assertEqual(plate['background'], 'opaque_black')
        self.assertEqual([r['path'] for r in plate['references']],
                         ['assets/reference/scenarios/puesto.png'])
        self.assertTrue((ROOT / plate['prompt_file']).read_text().strip())
        self.assertEqual(hashlib.sha256((ROOT / plate['path']).read_bytes()).hexdigest(),plate['sha256'])

    def test_missing_packs_are_not_misrepresented_as_installed(self):
        manifest = self.manifest()
        self.assertNotIn("floor", manifest["images"])
        self.assertEqual(manifest["placeholders"]["floor"]["rendering"], "pygame-code")
        self.assertEqual(manifest["not_integrated"]["sbs"]["reason"], "HTTP 429; no further requests")


if __name__ == "__main__":
    unittest.main()
