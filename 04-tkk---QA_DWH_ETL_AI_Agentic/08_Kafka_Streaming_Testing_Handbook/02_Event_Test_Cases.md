# Event Test Cases

| Scenario | Expected result |
|---|---|
| duplicate order event | one business effect; duplicate trace retained |
| late event inside window | correct revised aggregate or documented handling |
| late event outside window | dead letter/alert or contract behavior |
| consumer crash after read | safe retry without loss/duplicate sink state |
| incompatible schema | rejected before corrupting consumer state |
| replay from offset | approved final state and reconciliation |
