#include <stdio.h>
#include <pthread.h>

static volatile int r1 = 0, r2 = 0;
pthread_mutex_t m;

void* deposit1(void *args) {
    pthread_mutex_lock(&m);
    for (int i=0; i<1000000; i++)
    {
        ++r1;
    }
    return NULL;
}

void* deposit2(void *args) {
    pthread_mutex_lock(&m);
    for (int i=0; i<1000000; i++)
    {
        ++r2;
    }
    pthread_mutex_unlock(&m);
    return NULL;
}

int main() {
    pthread_t t1, t2;
    printf("App start work with r1 = %d, r2 = %d\r\n", r1, r2);

    pthread_create(&t1, NULL, deposit1, NULL);
    pthread_create(&t2, NULL, deposit2, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    printf("App finish work with r1 = %d, r2 = %d\r\n", r1, r2);
    return 0;
}
