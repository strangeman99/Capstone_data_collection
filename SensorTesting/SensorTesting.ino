#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;
int pulsePin = 18;
int pulse;

void setup(void) {
  pinMode(pulsePin, INPUT);  


  Serial.begin(115200);
  while (!Serial)
    delay(10);

  // Try to initialize!
  if (!mpu.begin()) {
    while (1) {
      delay(10);
    }
  }

  // Setting mpu params
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);

  delay(100);
}

void loop() {
  // Read sensors
  pulse = analogRead(pulsePin);
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  // Print values to be read by the Python script
  /*Serial.print("xaccel ");
  Serial.println(a.acceleration.x);
  Serial.print("yaccel ");
  Serial.println(a.acceleration.y);
  Serial.print("zaccel ");
  Serial.println(a.acceleration.z);
  Serial.print("xrot ");
  Serial.println(a.gyro.x);
  Serial.print("yrot ");
  Serial.println(a.gyro.y);
  Serial.print("zrot ");
  Serial.println(a.gyro.z);*/
  Serial.print("pulse ");
  Serial.println(pulse);
}
