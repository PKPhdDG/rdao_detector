#include <errno.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

FILE *f = NULL;

void *thread_test(void *args)
{
    errno = 0;
    f = fopen("logs.txt", "r");
    if (f == NULL)
    {
        const char *message = strerror(errno);
        printf("Cannot open the file. Reason: %s\n", message);
        return (void*)NULL;
    }
    puts("File opened");
    fclose(f);
    return (void*)NULL;
}

int main()
{
    pthread_t t1;
    pthread_create(&t1, NULL, thread_test, NULL);
    pthread_join(t1, NULL);
    return 0;
}
