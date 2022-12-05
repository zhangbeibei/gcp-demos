#!/bin/bash
# 使用 Google Cloud Certificate Manager 创建证书，使用该证书创建 LB

# 替换 DOMAIN_NAME 为你自己的域名
DOMAIN_NAME=""

########################################################################################################################
    # step1: create a google-managed certificate with DNS authorization #
########################################################################################################################

# 前提条件
# 需要提前创建好 DNS 公共托管区: https://cloud.google.com/dns/docs/zones#create-pub-zone

# 替换 DNS_ZONE_NAME 为你在 google cloud dns 创建的 public zone name
DNS_ZONE_NAME=""

# 替换 CERTIFICATE_NAME 为你自己的证书名，不能包含除了连字符之外的特殊符号
CERTIFICATE_NAME=""

AUTHORIZATION_NAME="$CERTIFICATE_NAME-auth"

# 创建 DNS 授权
gcloud certificate-manager dns-authorizations create ${AUTHORIZATION_NAME} \
    --domain=$DOMAIN_NAME
gcloud certificate-manager dns-authorizations describe ${AUTHORIZATION_NAME}

# 提取 DNS authorization 信息用来创建 DNS 记录
DNS_KEY=$(gcloud certificate-manager dns-authorizations describe $AUTHORIZATION_NAME \
	--format='value(dnsResourceRecord.name)')
DNS_VALUE=$(gcloud certificate-manager dns-authorizations describe $AUTHORIZATION_NAME \
    --format='value(dnsResourceRecord.data)')

# 如果你的DNS验证在Google Cloud DNS上，用以下命令添加 DNS cname 记录。如果在第三方DNS厂商，请在第三方 DNS 厂商添加 cname 记录
gcloud dns record-sets transaction start --zone=${DNS_ZONE_NAME}
gcloud dns record-sets transaction add $DNS_VALUE \
   --name=$DNS_KEY \
   --ttl="30" \
   --type="CNAME" \
   --zone=$DNS_ZONE_NAME
gcloud dns record-sets transaction execute --zone=${DNS_ZONE_NAME}

# 创建 google-managed 证书
gcloud certificate-manager certificates create ${CERTIFICATE_NAME} \
    --domains=${DOMAIN_NAME} --dns-authorizations=${AUTHORIZATION_NAME}

#验证证书状态
gcloud certificate-manager certificates describe ${CERTIFICATE_NAME}


########################################################################################################################
    # step2: create a https load balancer and attach the certificate #
########################################################################################################################

CERTIFICATE_MAP_NAME="$CERTIFICATE_NAME-map" 
CERTIFICATE_MAP_ENTRY_NAME"$CERTIFICATE_NAME-map-entry"

URL_MAP_NAME"$CERTIFICATE_NAME-url-map"
TARGET_PROXY_NAME="$CERTIFICATE_NAME-target-proxy"
FORWARDING_RULE="$CERTIFICATE_NAME-forwarding-rule"

# 创建证书映射 certification map
gcloud certificate-manager maps create ${CERTIFICATE_MAP_NAME}

# 创建 certification map entry
gcloud certificate-manager maps entries create ${CERTIFICATE_MAP_ENTRY_NAME} \
    --map=${CERTIFICATE_MAP_NAME} \
    --certificates=${CERTIFICATE_NAME} \
    --hostname=${DOMAIN_NAME}

# 验证 certification map entry
gcloud certificate-manager maps entries describe ${CERTIFICATE_MAP_ENTRY_NAME} \
    --map=${CERTIFICATE_MAP_NAME}

# 前提条件
# 提前创建好 backend service 后端服务，参考：https://cloud.google.com/load-balancing/docs/backend-service#internet_network_endpoint_groups

BACKEND_SERVICE_NAME=""

# 创建 url map
gcloud compute url-maps create ${URL_MAP_NAME} \
    --default-service=${BACKEND_SERVICE_NAME} \
    --global

# 创建 target_proxy
gcloud compute target-https-proxies create ${TARGET_PROXY_NAME} \
    --url-map=${URL_MAP_NAME} --certificate-map=${CERTIFICATE_MAP_NAME} \
    --global

#创建转发规则
gcloud compute forwarding-rules create ${FORWARDING_RULE} \
    --target-https-proxy=${TARGET_PROXY_NAME} \
    --global \
    --ports=443
