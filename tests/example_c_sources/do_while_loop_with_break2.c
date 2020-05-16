#include <stdio.h>

int main()
{
    int i=0;
    do
    {
        if (i > 99) {
            break;
        }
        else {
            printf("%d\n", i);
        }
        ++i;
    } while (i < 100);

    return 0;
}
