#include <pthread.h>
#include <stdbool.h>
#include <stdio.h>
#include <unistd.h>

extern pthread_mutex_t m;

void* t1f(void *args);
void* t2f(void *args);
