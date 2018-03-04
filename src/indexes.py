import src.storage as st


class Index:
    istorage = None
    indexes = None

    @staticmethod
    def init():
        if Index.istorage is None:
            Index.istorage = st.JINIStorage("indexes.conf")
            Index.indexes = Index.istorage.getall()
        return Index

    @staticmethod
    def get_indexes():
        return Index.indexes

    @staticmethod
    def post_index(index):
        Index.indexes[index["name"]] = index
        Index.indexes = Index.istorage.update(index["name"], index)
        return 0

    @staticmethod
    def add_index(index):
        Index.indexes = Index.istorage.add(index["name"], index)
        return index

    @staticmethod
    def get_index(name):
        Index.indexes = Index.istorage.getall()
        if name in Index.indexes:
            return Index.indexes[name]
        else:
            raise Exception("Index %s does not exist" % name)

    @staticmethod
    def del_job(name):
        Index.indexes = Index.istorage.delete(name)
        return 0


