from src.elastic_controller.index_crud import EIndex


ind, dat = EIndex.separate_date("filebeat-2018.02.18")
print(ind, dat)
exit(0)

indices = EIndex.get_indices()
for index in indices:
    ind = EIndex.get_index(index)
    break

EIndex.create_index("random_test")
indices = EIndex.get_indices()
if "random_test" not in indices:
    print("non")
print(indices)
EIndex.delete_index("random_test")