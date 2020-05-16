#include <stdio.h>

int main()
{
    int i=0;
    do
    {
        if (i < 99) {
            printf("%d\n", i);
        }
        else {
            break;
        }
        i += 1;
    } while (i < 100);

    return 0;
}
