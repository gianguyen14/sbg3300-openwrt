# SPDX-License-Identifier: GPL-2.0-only
include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=sbg3300-xtm
PKG_RELEASE:=1
PKG_LICENSE:=GPL-2.0-only
PKG_LICENSE_FILES:=COPYING

include $(INCLUDE_DIR)/package.mk

define KernelPackage/sbg3300-xtm
  SUBMENU:=Network Devices
  TITLE:=SBG3300 offline XTM DMA and PTM component
  DEPENDS:=@TARGET_bmips_bcm63268
  FILES:=$(PKG_BUILD_DIR)/sbg3300_xtm_dma.ko
  KCONFIG:=
endef

define KernelPackage/sbg3300-xtm/description
 Original DMA/ring and PTM netdev component. Requires a separately validated
 SAR/DSL controller owner. No automatic hardware attachment or module autoload.
 No PHY firmware, board topology or device runtime validation is included.
endef

define Build/Compile
	$(KERNEL_MAKE) M="$(PKG_BUILD_DIR)" W=1 KCFLAGS=-Werror modules
endef

$(eval $(call KernelPackage,sbg3300-xtm))
