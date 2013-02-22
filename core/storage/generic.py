class GenericStorage():
    def upload(self, file, name):
        raise NotImplementedError # pragma: no cover

    def download(self, url=None):
        raise NotImplementedError # pragma: no cover

    def delete(self, url=None):
        raise NotImplementedError # pragma: no cover
