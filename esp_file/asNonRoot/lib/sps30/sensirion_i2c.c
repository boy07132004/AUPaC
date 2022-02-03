#include "sensirion_arch_config.h"
#include "sensirion_common.h"
#include "sensirion_i2c.h"
#include "driver/i2c.h"


#define I2C_MASTER_NUM 					I2C_NUM_0   /*!< I2C port number for master dev */
#define I2C_MASTER_SCL_IO    			22    		/*!< gpio number for I2C master clock */
#define I2C_MASTER_SDA_IO    			21    		/*!< gpio number for I2C master data  */
#define I2C_MASTER_FREQ_HZ    			100000     	/*!< I2C master clock frequency */
#define I2C_MASTER_TX_BUF_DISABLE   	0   		/*!< I2C master do not need buffer */
#define I2C_MASTER_RX_BUF_DISABLE   	0   		/*!< I2C master do not need buffer */
#define WRITE_BIT  						I2C_MASTER_WRITE /*!< I2C master write */
#define READ_BIT   						I2C_MASTER_READ  /*!< I2C master read */
#define ACK_CHECK_EN   					0x1     /*!< I2C master will check ack from slave*/
#define ACK_CHECK_DIS  					0x0     /*!< I2C master will not check ack from slave */
#define ACK_VAL    						0x0         /*!< I2C ack value */
#define NACK_VAL                        0x1


int16_t sensirion_i2c_select_bus(uint8_t bus_idx) {
    // IMPLEMENT or leave empty if all sensors are located on one single bus
    return STATUS_FAIL;
}

void sensirion_i2c_init(void) {
    int i2c_master_port = I2C_MASTER_NUM;
	    i2c_config_t conf;
	    conf.mode = I2C_MODE_MASTER;
	    conf.sda_io_num = I2C_MASTER_SDA_IO;
	    conf.sda_pullup_en = GPIO_PULLUP_ENABLE;
	    conf.scl_io_num = I2C_MASTER_SCL_IO;
	    conf.scl_pullup_en = GPIO_PULLUP_ENABLE;
	    conf.master.clk_speed = I2C_MASTER_FREQ_HZ;
	    i2c_param_config(i2c_master_port, &conf);
	    i2c_driver_install(i2c_master_port, conf.mode,
	                       I2C_MASTER_RX_BUF_DISABLE,
	                       I2C_MASTER_TX_BUF_DISABLE, 0);
}

void sensirion_i2c_release(void) {
    // IMPLEMENT or leave empty if no resources need to be freed
}

int8_t sensirion_i2c_read(uint8_t address, uint8_t* data, uint16_t count) {
    if (count == 0) {
        return ESP_OK;
    }
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, ( address << 1 ) | READ_BIT, ACK_CHECK_EN);
    if (count > 1) {
        i2c_master_read(cmd, data, count - 1, ACK_VAL);
    }
    i2c_master_read_byte(cmd, data + count - 1, NACK_VAL);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, 1000 / portTICK_RATE_MS);
    i2c_cmd_link_delete(cmd);
    return ret;
}

int8_t sensirion_i2c_write(uint8_t address, const uint8_t* data,
                           uint16_t count) {

    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, ( address << 1 ) | WRITE_BIT, ACK_CHECK_EN);
    i2c_master_write(cmd, data, count, ACK_CHECK_EN);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_MASTER_NUM, cmd, 1000 / portTICK_RATE_MS);
    i2c_cmd_link_delete(cmd);
    return ret;
}

void sensirion_sleep_usec(uint32_t useconds) {
    vTaskDelay(useconds/1000);
}
