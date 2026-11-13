"""Testes offline do contrato de imagem. Nenhuma chamada ao upstream."""
from __future__ import annotations
import base64
import io
import json
from pathlib import Path
from unittest import TestCase, mock
import tempfile
import unittest
from urllib.error import HTTPError
from videoforge import proxy_images as p

# PNG 1x1 válido, sem qualquer imagem externa
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/T6sAAAAASUVORK5CYII=")


class FakeReply:
    def __init__(self, obj):
        self.data = io.BytesIO(json.dumps(obj).encode())
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None
    def read(self, size):
        return self.data.read(size)


class ProxyTests(TestCase):
    def test_reject_insecure_remote_endpoint(self):
        for url in ("http://example.com", "http://localhost:8080", "https://example.com@evil.org/x", "https://example.com/?secret=x"):
            with self.subTest(url=url), self.assertRaises(p.ProxyImageError):
                p.endpoint(url, "/health")
        self.assertEqual(p.endpoint("http://127.0.0.1:18080", "/health"), "http://127.0.0.1:18080/health")
        self.assertEqual(p.endpoint("https://proxy.example/v1", "/v1/images/generations"), "https://proxy.example/v1/images/generations")

    def test_channel_isolation(self):
        with self.assertRaises(p.ProxyImageError):
            p.destination("outro-canal", "episodio-001", "cena-01")
        for name in ("../fora", "um/dois", "", "A"):
            with self.subTest(name=name), self.assertRaises(p.ProxyImageError):
                p.destination("otaku-br", name, "cena-01")

    def test_valid_image_and_denied_url(self):
        data, suffix = p.decode_image({"data": [{"b64_json": base64.b64encode(PNG).decode()}]})
        self.assertEqual(data, PNG)
        self.assertEqual(suffix, ".png")
        with self.assertRaises(p.ProxyImageError):
            p.decode_image({"data": [{"url": "https://example.com/private.png"}]})

    def test_http_body_hidden(self):
        def reject(req, timeout):
            raise HTTPError(req.full_url, 429, "quota secret leaked?", None, None)
        with mock.patch.object(p.urllib.request, "urlopen", side_effect=reject):
            with self.assertRaises(p.ProxyImageError) as ctx:
                p.call_proxy("https://proxy.example", "/health", "a"*32)
        self.assertIn("429", str(ctx.exception))
        self.assertNotIn("secret", str(ctx.exception))

    def test_health_without_upstream(self):
        with mock.patch.object(p.urllib.request, "urlopen", return_value=FakeReply({"status": "ok", "accounts": 1})):
            p.health("https://proxy.example", "a"*32)
        with mock.patch.object(p.urllib.request, "urlopen", return_value=FakeReply({"status": "ok", "accounts": 0})):
            with self.assertRaises(p.ProxyImageError):
                p.health("https://proxy.example", "a"*32)

    def test_generate_artifact_scoped_and_no_secret(self):
        with tempfile.TemporaryDirectory() as folder, mock.patch.object(p, "ROOT", Path(folder)):
            config = Path(folder) / "canal/otaku-br/canal.json"
            config.parent.mkdir(parents=True)
            config.write_text('{"id":"otaku-br"}')
            with mock.patch.object(p.urllib.request, "urlopen", return_value=FakeReply({
                "data": [{"b64_json": base64.b64encode(PNG).decode()}]
            })):
                dest = p.generate("https://proxy.example", "a"*32, "otaku-br",
                    "video-001", "cena-01", "gpt-image-2", "1024x1536",
                    "Um prompt original de ilustracao para teste")
            self.assertTrue(dest.is_file())
            self.assertIn("output/otaku-br/videos/video-001/imagens/cena-01.png", dest.as_posix())
            report = dest.with_suffix(".meta.json").read_text()
            self.assertNotIn("a"*32, report)
            self.assertNotIn("prompt original", report)
            self.assertEqual(json.loads(report)["sha256"], p.hashlib.sha256(PNG).hexdigest())


if __name__ == "__main__":
    unittest.main()
