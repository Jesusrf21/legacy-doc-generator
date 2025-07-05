/**
 * Clase que representa una cuenta bancaria simple.
 */
public class CuentaBancaria {
    private String titular;
    private double saldo;
    private int numeroCuenta;

    public CuentaBancaria(String titular, double saldoInicial, int numeroCuenta) {
        this.titular = titular;
        this.saldo = saldoInicial;
        this.numeroCuenta = numeroCuenta;
    }

    public void depositar(double cantidad) {
        if (cantidad > 0) {
            saldo += cantidad;
            System.out.println("Depósito exitoso de " + cantidad);
        }
    }

    public void retirar(double cantidad) {
        if (cantidad > 0 && saldo >= cantidad) {
            saldo -= cantidad;
            System.out.println("Retiro exitoso de " + cantidad);
        }
    }

    public void mostrarResumen() {
        System.out.println("Titular: " + titular);
        System.out.println("Saldo: " + saldo);
    }

    public void transferir(CuentaBancaria destino, double cantidad) {
        if (saldo >= cantidad && cantidad > 0) {
            this.retirar(cantidad);
            destino.depositar(cantidad);
            System.out.println("Transferencia realizada");
        }
    }
}

class Banco {
    public static void main(String[] args) {
        CuentaBancaria cuenta1 = new CuentaBancaria("Lucía", 1500.0, 1001);
        CuentaBancaria cuenta2 = new CuentaBancaria("Pedro", 1000.0, 1002);

        cuenta1.depositar(500);
        cuenta1.retirar(200);
        cuenta1.transferir(cuenta2, 300);
    }
}
