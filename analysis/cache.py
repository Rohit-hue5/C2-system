import time

class AnalysisCache:
    def __init__(self):
        self.cache = {}

    def is_cached(self, sample_hash):
        if sample_hash in self.cache:
            if time.time() - self.cache[sample_hash]['timestamp'] < 86400:
                return True
        return False

    def get_analysis(self, sample_hash):
        return self.cache.get(sample_hash, {})

    def store(self, sample_hash, result):
        result['timestamp'] = time.time()
        self.cache[sample_hash] = result

    def get_recent(self):
        return list(self.cache.values())[-10:]
