#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if(argc != 2) {
        fprintf(stderr, "usage: sleeper <seconds>\n");
        exit(1);
    }
    int delay = atoi(argv[1]);
    if(delay == 0) {
        fprintf(stderr, "error: <seconds> must be an int > 0\n");
        exit(2);
    }
    sleep(delay);
}
