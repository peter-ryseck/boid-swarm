#ifndef UTILS_H
#define UTILS_H

float GetRandomFloat(float min, float max);
float Distance(Boid* boid1, Boid* boid2);
float LimitVector(float *vx, float *vy, float max);
float Magnitude(float *vx, float *vy, float *mag);
float Normalize(float *vx, float *vy);

#endif
