# Hardware acceleration

Stock runtime loads Broadcom FAP/BPM/ingress-QoS modules and initializes two
FAP cores. These are vendor acceleration components, not evidence of a directly
portable OpenWrt HNAT implementation. Current bmips OpenWrt bring-up should be
software routed first; FAP/HNAT is a separate later porting effort after
networking and throughput baselines exist.

Status: `VENDOR-ONLY / PORTABILITY UNKNOWN`. No acceleration patches are applied.
