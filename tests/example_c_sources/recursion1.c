#include <stdio.h>
#include <pthread.h>

static volatile long long result;

int sum(int n);
void *thread(void *args);

int main() {
    int number;

    printf("Enter a positive integer: ");
    scanf("%d", &number);

    pthread_t t;
    pthread_create(&t, NULL, thread, &number);
    pthread_join(t, NULL);

    printf("sum = %d", result);
    return 0;
}

int sum(int n) {
    if (n != 0)
        // sum() function calls itself
        return n + sum(n-1);
    else
        return n;
}

void *thread(void *args)
{
    int start_val = *(int*)args;
    result = sum(start_val);
    return NULL;
}
