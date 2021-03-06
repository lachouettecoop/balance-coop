import axios from 'axios';
import serverUrl from './url';

function print(product, nb, weight, discount, cut) {
  return axios({
    method: 'post',
    url: `${serverUrl()}/print_label`,
    data: {
      product, nb, weight, discount, cut,
    },
  });
}

export default print;
