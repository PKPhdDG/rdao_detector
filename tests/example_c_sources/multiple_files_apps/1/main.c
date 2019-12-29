#include <threads.h>

int main() {
    pthread_t t1, t2;
    const char fname[] = "logfile.txt";

    pthread_create(&t1, NULL, t1f, (void *)fname);
    pthread_create(&t2, NULL, t2f, (void *)fname);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}
