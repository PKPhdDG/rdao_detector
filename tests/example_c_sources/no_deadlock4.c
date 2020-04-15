#include <stdio.h>
#include <pthread.h>

static volatile int r1 = 0;
pthread_mutex_t m, n;

void* deposit1(void *args) {
    int i=0;
    pthread_mutex_lock(&m);
    pthread_mutex_unlock(&m);
    pthread_mutex_lock(&n);
    do
    {
        ++r1, ++i;
    } while (i<1000000);
    pthread_mutex_unlock(&n);
    pthread_mutex_lock(&m);
    pthread_mutex_unlock(&m);
    return NULL;
}

int main() {
    pthread_t t1;
    printf("App start work with r1 = %d\r\n", r1);
    pthread_create(&t1, NULL, deposit1, NULL);
    pthread_join(t1, NULL);
    printf("App finish work with r1 = %d\r\n", r1);
    return 0;
}
