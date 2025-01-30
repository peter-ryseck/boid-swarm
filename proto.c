// clang -o proto proto.c -I/opt/homebrew/include/SDL2 -L/opt/homebrew/lib -lSDL2
// ./proto
// gcc -o proto proto.c -I/opt/homebrew/include/SDL2 -L/opt/homebrew/lib -L/opt/homebrew/opt/openblas/lib -I/opt/homebrew/opt/openblas/include -lopenblas -lSDL2
// ./proto
#include <SDL.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <time.h>

#define NUM_PARTICLES 10000
#define NUM_ITERATIONS 100
#define DIMENSIONS 2
#define W 0.6           // Inertia weight
#define C1 0.6          // Cognitive (personal) coefficient
#define C2 0.6          // Social (global) coefficient
#define X_MIN -10.0     // Minimum boundary of search space
#define X_MAX 10.0      // Maximum boundary of search space
#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 600
#define CIRCLE_RADIUS 2

typedef struct {
    float position[DIMENSIONS];
    float velocity[DIMENSIONS];
    float bestPosition[DIMENSIONS];
    float bestValue;
} Particle;

// Objective function: f(x, y) = sin(x) * cos(y) + (x^2 + y^2) / 10
float objectiveFunction(float *position) {
    float x = position[0];
    float y = position[1];
    return sin(x) * cos(y) + (x * x + y * y) / 10.0;
}

// Random number generator between min and max
float randomfloat(float min, float max) {
    return min + ((float)rand() / RAND_MAX) * (max - min);
}

void initializeParticles(Particle particles[]) {
    for (int i = 0; i < NUM_PARTICLES; i++) {
        for (int d = 0; d < DIMENSIONS; d++) {
            particles[i].position[d] = randomfloat(X_MIN, X_MAX);
            particles[i].velocity[d] = randomfloat(-1.0, 1.0);
            particles[i].bestPosition[d] = particles[i].position[d];
        }
        particles[i].bestValue = objectiveFunction(particles[i].position);
    }
}

void updateParticle(Particle *particle, float *globalBestPosition) {
    for (int d = 0; d < DIMENSIONS; d++) {
        float r1 = randomfloat(0.0, 1.0);
        float r2 = randomfloat(0.0, 1.0);

        particle->velocity[d] = W * particle->velocity[d]
                                + C1 * r1 * (particle->bestPosition[d] - particle->position[d])
                                + C2 * r2 * (globalBestPosition[d] - particle->position[d]);

        particle->position[d] += particle->velocity[d]*0.1;

        // Keep particles within bounds
        if (particle->position[d] < X_MIN) particle->position[d] = X_MIN;
        if (particle->position[d] > X_MAX) particle->position[d] = X_MAX;
    }

    float value = objectiveFunction(particle->position);
    if (value < particle->bestValue) {
        particle->bestValue = value;
        for (int d = 0; d < DIMENSIONS; d++) {
            particle->bestPosition[d] = particle->position[d];
        }
    }
}

void drawCircle(SDL_Renderer *renderer, int centerX, int centerY, int radius) {
    for (int w = 0; w < radius * 2; w++) {
        for (int h = 0; h < radius * 2; h++) {
            int dx = radius - w; // Distance from the center in the x-axis
            int dy = radius - h; // Distance from the center in the y-axis
            if ((dx * dx + dy * dy) <= (radius * radius)) {
                SDL_RenderDrawPoint(renderer, centerX + dx, centerY + dy);
            }
        }
    }
}

int main() {
    srand((unsigned int)time(NULL));

    Particle* particles = malloc(NUM_PARTICLES * sizeof(Particle));
    initializeParticles(particles);

    float globalBestPosition[DIMENSIONS];
    float globalBestValue = DBL_MAX;

    // Find initial global best
    for (int i = 0; i < NUM_PARTICLES; i++) {
        if (particles[i].bestValue < globalBestValue) {
            globalBestValue = particles[i].bestValue;
            for (int d = 0; d < DIMENSIONS; d++) {
                globalBestPosition[d] = particles[i].bestPosition[d];
            }
        }
    }

    // Initialize SDL
    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        printf("SDL_Init Error: %s\n", SDL_GetError());
        return 1;
    }

    SDL_Window *win = SDL_CreateWindow("Particle Visualization", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, SCREEN_WIDTH, SCREEN_HEIGHT, SDL_WINDOW_SHOWN);
    if (win == NULL) {
        fprintf(stderr, "SDL_CreateWindow Error: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }
    if (!win) {
        printf("SDL_CreateWindow Error: %s\n", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    SDL_Renderer *ren = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (!ren) {
        printf("SDL_CreateRenderer Error: %s\n", SDL_GetError());
        SDL_DestroyWindow(win);
        SDL_Quit();
        return 1;
    }

    int running = 1;

    SDL_Event event;

    clock_t totalStartTime = clock(); // Start total timer

    for (int iter = 0; iter < NUM_ITERATIONS; iter++) {
        // Handle events
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = 0;
            }
        }

        for (int i = 0; i < NUM_PARTICLES; i++) {
            updateParticle(&particles[i], globalBestPosition);
            if (particles[i].bestValue < globalBestValue) {
                globalBestValue = particles[i].bestValue;
                for (int d = 0; d < DIMENSIONS; d++) {
                    globalBestPosition[d] = particles[i].bestPosition[d];
                }
            }
        }

        // Clear screen
        SDL_SetRenderDrawColor(ren, 0, 0, 0, 255);
        SDL_RenderClear(ren);

        // Render particle[0]
        SDL_SetRenderDrawColor(ren, 255, 255, 255, 255); // White color
        for (int i = 0; i < NUM_PARTICLES; i++) {
            drawCircle(ren, particles[i].position[0]*100 + SCREEN_WIDTH/2, particles[i].position[1]*100 + SCREEN_HEIGHT/2, CIRCLE_RADIUS);
        }

        // Present the renderer
        SDL_RenderPresent(ren);

        // Delay for visualization
        SDL_Delay(10);
    }

    clock_t totalEndTime = clock(); // End total timer
    double totalTime = (double)(totalEndTime - totalStartTime) / CLOCKS_PER_SEC;
    printf("Total execution time for %d particles: %.4f seconds.\n", NUM_PARTICLES, totalTime);

    // Clean up
    SDL_DestroyRenderer(ren);
    SDL_DestroyWindow(win);
    SDL_Quit();

    free(particles);

    return 0;
}
