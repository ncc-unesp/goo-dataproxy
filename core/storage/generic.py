class GenericStorage():
    def upload(self, file, name):
        raise NotImplementedError

    def download(self, file):
        raise NotImplementedError

    def delete(self, url=None):
        raise NotImplementedError
