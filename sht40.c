#include <stdio.h>
#include <stdint.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/i2c-dev.h>
#include <sys/ioctl.h>

#define SHT40_ADDR 0x44
#define I2C_BUS "/dev/i2c-1"

float temperature = 0;
float humidity = 0;

int read_sht40(void) {
    int fd;
    uint8_t cmd = 0xFD;  // High precision measurement
    uint8_t data[6];

    // Open I2C bus
    if ((fd = open(I2C_BUS, O_RDWR)) < 0) {
        printf("Failed to open I2C bus\n");
        return -1;
    }

    // Set I2C device address
    if (ioctl(fd, I2C_SLAVE, SHT40_ADDR) < 0) {
        printf("Failed to acquire bus access\n");
        close(fd);
        return -1;
    }

    // Send measurement command
    if (write(fd, &cmd, 1) != 1) {
        printf("Error writing to I2C slave\n");
        close(fd);
        return -1;
    }

    // Wait for measurement
    usleep(10000);

    // Read data
    if (read(fd, data, 6) != 6) {
        printf("Error reading from I2C slave\n");
        close(fd);
        return -1;
    }

    close(fd);

    // Convert temperature
    uint16_t temp_raw = (data[0] << 8) | data[1];
    temperature = -45.0f + 175.0f * temp_raw / 65535.0f;

    // Convert humidity
    uint16_t hum_raw = (data[3] << 8) | data[4];
    humidity = 125.0f * hum_raw / 65535.0f;

    return 0;
}

int main() {
    if (read_sht40() == 0) {
        printf("%.2f\n%.2f\n", temperature, humidity);
        return 0;
    }
    return 1;
}