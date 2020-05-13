#include <stdio.h>
#include <pthread.h>

static volatile long long result;
pthread_mutex_t m;

int sum(int n);
void *thread(void *args);

int main() {
    int number;

    printf("Enter a positive integer: ");
    scanf("%d", &number);

    pthread_t t;
    pthread_create(&t, NULL, thread, &number);
    pthread_join(t, NULL);

    printf("Sum = %lld", result);
    return 0;
}

int sum(int n) {
    pthread_mutex_lock(&m);
    if (n != 0)
        return n + sum(n-1);
    else
        return n;
    pthread_mutex_unlock(&m);
}

void *thread(void *args)
{
    int start_val = *(int*)args;
    result = sum(start_val);
    return NULL;
}
