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
    } while (++i < 100);

    return 0;
}
