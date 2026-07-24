// Diseños de botones
export type ButtonVariant = 'primary' | 'secondary' | 'danger';

// Creamos una función para definir nuestro diseño y la exportaremos
export function buttonVariantClasses(variant: ButtonVariant): string {
  switch (variant) {
    case 'primary': return 'bg-amber-500 text-white hover:bg-amber-600 hover:text-gray-100 ';
    case 'secondary': return 'border border-amber-500 text-amber-500 hover:bg-amber-500 hover:text-white';
    case 'danger': return 'bg-red-600 text-white hover:bg-red-700 hover:text-gray-100 ';
  }
}
