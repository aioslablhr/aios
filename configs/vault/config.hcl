storage "raft" {
  path = "/vault/file"
  node_id = "aios-vault-1"
}

listener "tcp" {
  address     = "0.0.0.0:8210"
  tls_disable = true
}

disable_mlock = true
api_addr      = "http://10.0.0.100:8210"
cluster_addr  = "https://10.0.0.100:8211"
ui            = true
