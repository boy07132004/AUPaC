idf_component_register(SRCS
			"node.c"
			"../lib/sps30/sps30.c"
			"../lib/sps30/sensirion_common.c"
			"../lib/sps30/sensirion_i2c.c"
				INCLUDE_DIRS "../"
				REQUIRES mcommon mconfig mwifi mlink
)
