import src.sparkcontroller.webreq as wr


class EIndex:
    URL = "http://localhost:9200"
    HEADER = {
    }

    @staticmethod
    def create_index(name):
        url = "{url}/{index}".format(url=EIndex.URL, index=name)
        wr.put_req(url)

    @staticmethod
    def delete_index(name):
        url = "{url}/{index}".format(url=EIndex.URL, index=name)
        wr.delete_req(url)

    @staticmethod
    def get_index(name):
        url = "{url}/{index}".format(url=EIndex.URL, index=name)
        resp = wr.get_req(url)
        return resp.json()

    @staticmethod
    def get_indices():
        url = "{url}/_aliases".format(url=EIndex.URL)
        resp = wr.get_req(url)
        index_list = []
        for index in resp.json():
            index_list.append(index)
        return index_list

    @staticmethod
    def unique_indices(indices):
        pass

    @staticmethod
    def separate_date(name):
        pos = name.rfind("-")
        return name[:pos], name[pos+1:]

    @staticmethod
    def indices_cdates(indices):
        index_date = {}
        for index in indices:
            index_name, date = EIndex.separate_date(index)
            index_date[index] = date
        return index_date

    @staticmethod
    def get_index_regex(regex):
        pass

    @staticmethod
    def get_old_indices_byname(name):
        pass

    @staticmethod
    def get_old_indices():
        pass



