/* Prints the message of the day.
 *
 * Installed SUID root so any account can read the operator notice. It calls
 * `cat` without an absolute path, so it resolves the name through PATH -- which
 * is the escalation: a caller who controls PATH chooses which `cat` runs, and
 * it runs as root. */
#include <stdlib.h>
#include <unistd.h>

int main(void) {
    setuid(0);
    setgid(0);
    system("cat /etc/motd");
    return 0;
}
