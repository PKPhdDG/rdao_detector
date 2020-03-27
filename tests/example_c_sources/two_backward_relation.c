#include <errno.h>
#include <math.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

FILE *f = NULL;

void *thread_test(void *args)
{
    long int seed = time(0);
    srand(seed);
    size_t random_value = rand();
    errno = 0;
    f = fopen("logs.txt", "r");
    if (f == NULL)
    {
        const char *message = strerror(errno);
        printf("Cannot open the file. Reason: %s\r\n", message);
        return (void*)NULL;
    }
    puts("File opened");
    fclose(f);
    printf("File closed. Seed used in operations: %d\r\n", random_value);
    return (void*)NULL;
}

int main()
{
    pthread_t t1;
    pthread_create(&t1, NULL, thread_test, NULL);
    pthread_join(t1, NULL);
    return 0;
}
