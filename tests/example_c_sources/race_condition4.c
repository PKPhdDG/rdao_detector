#include <stdio.h>
#include <pthread.h>

static volatile int r1 = 0;

void* deposit1(void *args) {
    for (int i=0; i<1000000; i++)
    {
        ++r1;
    }
    return NULL;
}

int main() {
    pthread_t worker1, worker2, worker3, worker4;
    printf("App start work with r1 = %d\n", r1);

    pthread_create(&worker1, NULL, deposit1, NULL);
    pthread_create(&worker2, NULL, deposit1, NULL);
    pthread_create(&worker3, NULL, deposit1, NULL);
    pthread_create(&worker4, NULL, deposit1, NULL);

    pthread_join(worker1, NULL);
    pthread_join(worker2, NULL);
    pthread_join(worker3, NULL);
    pthread_join(worker4, NULL);

    printf("App finish work with r1 = %d\n", r1);
    return 0;
}
