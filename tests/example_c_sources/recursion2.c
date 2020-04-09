#include <stdio.h>
#include <pthread.h>

static volatile long long result;

int sum(int n);
int logN(int n);
void *thread(void *args);

int main() {
    int number;

    printf("Enter a positive integer: ");
    scanf("%d", &number);

    pthread_t t;
    pthread_create(&t, NULL, thread, &number);
    pthread_join(t, NULL);

    printf("Sum = %d", result);
    return 0;
}

int sum(int n) {
    if (n == 0)
        return n;
    else
        return n + logN(n-1);
}

int logN(int n)
{
    printf("Step: %d\n", n);
    return sum(n);
}

void *thread(void *args)
{
    int start_val = *(int*)args;
    result = logN(start_val);
    return NULL;
}
