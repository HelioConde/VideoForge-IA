from pathlib import Path
import tempfile
import unittest

from orchestrator import runtime
from orchestrator.runtime_store import Store
from orchestrator.runtime_issues import publish
from orchestrator.github_state import GitHubStateError


class FakeGitHub:
    API = 'https://api.github.com'
    repo = 'example/repo'
    def __init__(self,fail=False):
        self.comments = []
        self.posts = 0
        self.fail = fail
    def _request(self,method,url,payload=None):
        if method == 'POST':
            self.posts += 1
            if self.fail:
                raise GitHubStateError('ambiguous POST')
            comment = dict(payload,id=len(self.comments)+1)
            self.comments.append(comment)
            return 201,comment
        return (200,self.comments) if '/comments?' in url else (200,{'state':'open'})


class IssueTests(unittest.TestCase):
    def test_durable_intent_prevents_post_replay_and_reconciles_success(self):
        for fail in (False,True):
            with self.subTest(fail=fail),tempfile.TemporaryDirectory() as tmp:
                store = Store(Path(tmp)/'db.sqlite',persist_callback=lambda snapshot:None)
                runtime.seed(store)
                runtime.step(store)
                runtime.step(store)
                client = FakeGitHub(fail)
                if fail:
                    with self.assertRaises(GitHubStateError):
                        publish(store,72,client)
                else:
                    publish(store,72,client)
                publish(store,72,client)
                self.assertEqual(client.posts,1)
                store.close()

    def test_publication_without_remote_persistence_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = Store(Path(tmp)/'db.sqlite')
            with self.assertRaises(ValueError):
                publish(store,72,FakeGitHub())
            store.close()
