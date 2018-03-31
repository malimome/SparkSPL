bin/elasticsearch-plugin install x-pack
bin/elasticsearch
bin/x-pack/setup-passwords auto
## copy the password for users

bin/kibana-plugin install x-pack

# add user pass to kibana.yml

bin/kibana
